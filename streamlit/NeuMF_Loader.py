import torch
import pandas as pd
import numpy as np
import os
import importlib
from recbole.config import Config
from recbole.data.dataset import Dataset
from recbole.data.interaction import Interaction
from recbole.data.utils import create_dataset
from recbole.utils import get_model
import os
import json



MODEL_PATH_4th = './models/NeuMF_model/NeuMF-May-31-2025_11-08-41.pth'

USER_RATINGS_FILE_JSON_PATH = '../../user_ratings.json'

CONFIG_DICT_4th = {
    'model': 'NeuMF',
    'dataset': 'movielens', 
    'data_path': './models/NeuMF_model/',

    'field_separator': '\t',
    'USER_ID_FIELD': 'user_id',
    'ITEM_ID_FIELD': 'item_id',
    'RATING_FIELD': 'rating',
    'TIME_FIELD': 'timestamp',

    'load_col': {
        'inter': ['user_id', 'item_id', 'rating', 'timestamp']
    },
    'LABEL_FIELD': 'rating',
    'threshold': {'rating': 4.5}, # Ratings >= 4.5 are positive interactions for ranking

    'eval_task': 'ranking',
    'normalize_field': {},
    'loss_type': 'BPR',

    'eval_args': {
        'split': {'RS': [0.9, 0.05, 0.05]}, # This will be overridden for custom evaluation
        'order': 'TO',
        'group_by': 'user',
        'neg_sample_args': None,
        'topk': [10, 20, 50],
    },

    'metrics': ['Recall', 'NDCG', 'MRR'],
    'valid_metric': 'NDCG@10',
    'valid_metric_bigger': True,

    'train_neg_sample_args': {'distribution': 'uniform', 'sample_num': 1},

    'mf_embedding_size': 64,
    'mlp_embedding_size': 64,
    'layers': [128, 64, 32],
    'dropout_prob': 0.3,

    'learning_rate': 0.001,
    'train_batch_size': 1024,
    'epochs': 14,
    'eval_step': 5,

    'eval_batch_size': 512,
}

# --- Function to Initialize and Load the Model ---
def initialize_NeuMF_model(model_path: str= None, config_dict: dict = None) -> (torch.nn.Module, Dataset):
    """
    Initializes a RecBole model and loads its state dictionary from a checkpoint.

    Args:
        model_path (str): The path to the saved PyTorch model checkpoint (.pth file).
                                    If None, uses MODEL_PATH_4th as default.            
        config_dict (dict, optional): A dictionary containing configuration parameters
                                     for the RecBole model. If None, uses CONFIG_DICT_4th.

    Returns:
        tuple: A tuple containing:
            - model (torch.nn.Module): The loaded RecBole model.
            - dataset (recbole.data.dataset.Dataset): The dataset object initialized
                                                      with the provided configuration.
    """
    if model_path is None:
        model_path = MODEL_PATH_4th
    if config_dict is None:
        config_dict = CONFIG_DICT_4th.copy() # Use a copy to avoid modifying global config

    config = Config(model=config_dict['model'], dataset=config_dict['dataset'], config_dict=config_dict)
    dataset = create_dataset(config)

    model_class = get_model(config['model'])
    model = model_class(config, dataset)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model checkpoint not found at: {model_path}")

    checkpoint = torch.load(model_path, weights_only=False, map_location=torch.device('cpu')) # Load to CPU
    model.load_state_dict(checkpoint['state_dict'])

    model.eval()

    return model, dataset


def predict_for_cold_start_user_from_json(model: torch.nn.Module, dataset: Dataset, user_ratings_file: str) -> pd.DataFrame:
    """
    Generates predictions for a new (cold-start) user whose ratings are provided in a JSON file.
    This function creates a synthetic user embedding by averaging the embeddings of items
    the user has rated, then uses this to predict scores for unrated items.

    Args:
        model (torch.nn.Module): The loaded RecBole model.
        dataset (recbole.data.dataset.Dataset): The main dataset object used by the model,
                                                containing ID mappings.
        user_ratings_file (str): Path to the user_ratings.json file.

    Returns:
        pd.DataFrame: DataFrame containing 'movieId', 'predicted_score', and 'predicted_rating'
                      for the unrated items, sorted by predicted_rating.
    """

    try:
        with open(user_ratings_file, 'r') as f:
            user_raw_ratings = json.load(f)
    except FileNotFoundError:
        return pd.DataFrame()
    except json.JSONDecodeError:
        return pd.DataFrame()

    rated_item_raw_ids = [str(k) for k in user_raw_ratings.keys()]
    
    rated_item_internal_ids = []
    for item_raw_id in rated_item_raw_ids:
        try:
            internal_id = dataset.token2id(dataset.iid_field, item_raw_id)
            rated_item_internal_ids.append(internal_id)
        except KeyError:
            print(f"Warning: Item '{item_raw_id}' from user_ratings.json not found in model's item vocabulary. Skipping.")
    
    if not rated_item_internal_ids:
        print("No valid rated items found in the user's history for prediction.")
        return pd.DataFrame()

    if not hasattr(model, 'item_mf_embedding') or not hasattr(model, 'item_mlp_embedding'):
        print("Error: Model does not have expected item embedding layers (item_mf_embedding, item_mlp_embedding). Cannot derive synthetic user embedding.")
        return pd.DataFrame()

    item_mf_embeddings = model.item_mf_embedding.weight.data[rated_item_internal_ids].cpu()
    item_mlp_embeddings = model.item_mlp_embedding.weight.data[rated_item_internal_ids].cpu()

    synthetic_user_mf_embedding = item_mf_embeddings.mean(dim=0, keepdim=True)
    synthetic_user_mlp_embedding = item_mlp_embeddings.mean(dim=0, keepdim=True)

    all_item_internal_ids = torch.arange(1, dataset.item_num, dtype=torch.long)
    unrated_item_internal_ids = [
        item_id for item_id in all_item_internal_ids.tolist()
        if item_id not in rated_item_internal_ids
    ]
    
    if not unrated_item_internal_ids:
        print("No unrated items to recommend for this user.")
        return pd.DataFrame()

    candidate_item_internal_ids_tensor = torch.tensor(unrated_item_internal_ids, dtype=torch.long)

    candidate_item_mf_embeddings = model.item_mf_embedding.weight.data[candidate_item_internal_ids_tensor].cpu()
    candidate_item_mlp_embeddings = model.item_mlp_embedding.weight.data[candidate_item_internal_ids_tensor].cpu()

    expanded_user_mf_embedding = synthetic_user_mf_embedding.expand_as(candidate_item_mf_embeddings)
    expanded_user_mlp_embedding = synthetic_user_mlp_embedding.expand_as(candidate_item_mlp_embeddings)

    with torch.no_grad():
        mf_vector = expanded_user_mf_embedding * candidate_item_mf_embeddings
        mlp_vector = torch.cat((expanded_user_mlp_embedding, candidate_item_mlp_embeddings), dim=-1)
        mlp_vector = model.mlp_layers(mlp_vector)
        output_vector = torch.cat((mf_vector, mlp_vector), dim=-1)
        predicted_scores_tensor = model.predict_layer(output_vector).squeeze(-1)

    predicted_scores = predicted_scores_tensor.tolist()

    predictions_data = []
    for i, score in enumerate(predicted_scores):
        item_internal_id = unrated_item_internal_ids[i]
        item_raw_id = dataset.id2token(dataset.iid_field, item_internal_id)
        predictions_data.append({
            'movieId': item_raw_id,
            'predicted_score': score
        })

    predictions_df = pd.DataFrame(predictions_data).sort_values(by='predicted_score', ascending=False).head(50)
    predictions_df['predicted_rating'] = predictions_df['predicted_score']/predictions_df['predicted_score'].max() * 5.0
    return predictions_df


if __name__ == "__main__":
    f = 1