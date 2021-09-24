import argparse
import os
import warnings

from kerascls.config import ConfigReader
from kerascls.loss_and_metric import load_optimizer, load_loss, load_list_metric

if __name__ == '__main__':
    package_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, help='Config path')
    parser.set_defaults(config=os.path.join(package_dir, "configs", "setting.cfg"))

    config_reader = ConfigReader(parser.parse_args().config)
    optimizer_info = config_reader.get_optimizer()
    loss_info = config_reader.get_loss()
    list_metric_info = config_reader.get_list_metric()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        print("-------------------------------Optimizer-------------------------------")
        print(load_optimizer(**optimizer_info).get_config())
        print("")
        print("---------------------------------Loss---------------------------------")
        print(load_loss(**loss_info).get_config())
        print("")
        print("--------------------------------Metrics--------------------------------")
        list_metric = load_list_metric(list_metric_info)
        for metric in list_metric:
            if metric != 'accuracy':
                print(metric.get_config())
