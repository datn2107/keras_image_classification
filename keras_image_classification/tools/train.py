import argparse
import os

import pandas as pd

from keras_classification.utils.config import ConfigReader
from keras_classification.utils.data import split_and_load_dataset
from keras_classification.utils.evaluation import evaluate, save_result, plot_log_csv
from keras_classification.utils.model import KerasModel
from keras_classification.utils.prepare_training import compile_model, load_checkpoint, load_callbacks

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, help='Checkpoint Direction')
    parser.set_defaults(config=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../setting.cfg"))

    config_reader = ConfigReader(parser.parse_args().config)
    path_info = config_reader.get_path_config()
    data_info = config_reader.get_data_config()
    model_info = config_reader.get_model_config()
    optimizer_info = config_reader.get_optimizer_config()
    loss_info = config_reader.get_loss_config()
    list_metric_info = config_reader.get_list_metric_config()

    saving_dir = path_info['saving_dir']
    model_cp_dir = path_info['model_cp_dir']
    weights_cp_path = path_info['weights_cp_path']
    dataframe = pd.read_csv(path_info['metadata_path'], index_col=0)

    # Load model and data
    model_generator = KerasModel(**model_info, num_class=len(dataframe.columns))
    model = model_generator.create_model_keras()

    # input_shape of model [batch, height, width, channel]
    input_shape = model.input_shape
    train_dataset, val_dataset, test_dataset = split_and_load_dataset(dataframe, path_info['image_path'],
                                                                      batch_size=int(data_info['batch_size']),
                                                                      height=input_shape[1], width=input_shape[2])

    # Compile Model
    model = compile_model(model, optimizer_info=optimizer_info, loss_info=loss_info, list_metric_info=list_metric_info)
    model = load_checkpoint(model, model_cp_dir=model_cp_dir, weights_cp_path=weights_cp_path)
    loss_lastest_checkpoint = evaluate(model, val_dataset, model_cp_dir=model_cp_dir, weights_cp_path=weights_cp_path)

    # Training
    history = model.fit(
        train_dataset,
        epochs=data_info['epoch'],
        validation_data=val_dataset,
        initial_epoch=data_info['last_epoch'],
        callbacks=load_callbacks(saving_dir, loss_lastest_checkpoint=loss_lastest_checkpoint)
    )

    best_model_path = os.path.join(saving_dir, "save_model", "best")
    result = evaluate(model, test_dataset, model_cp_dir=best_model_path)
    print(result)

    plot_log_csv(os.path.join(saving_dir, "log.csv"))
    save_result(result=result, saving_dir=saving_dir, model_name=model_info['model_name'])
