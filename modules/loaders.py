import os
import json
import nacos
import yaml
from abc import abstractmethod


try:
    from modules.loggers import sysmtem_log

    print_err = sysmtem_log.error
except ImportError:
    print_err = print


class Dict2Object:
    def __init__(self, dictionary: dict):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, Dict2Object(value))
            else:
                setattr(self, key, value)

    def __getattr__(self, __name: str):
        if __name in self.__dict__:
            return self.__dict__[__name]
        return None


class NacosSchemaLoader:
    def __init__(self, standalone=False):
        """TODO: 初始化配置信息"""
        self._data_id = os.getenv("nacos_data_id")
        self._group = os.getenv("nacos_group")
        # self.add_config_watcher(standalone)

    @property
    def client(self):
        return nacos.NacosClient(
            os.getenv("nacos_addr"),
            namespace=os.getenv("env"),
            username=os.getenv("nacos_user"),
            password=os.getenv("nacos_password"),
        )

    @abstractmethod
    def download_from_nacos(self) -> dict:
        """下载配置信息"""

    @abstractmethod
    def upload_to_nacos(self, config) -> None:
        """上传配置信息"""

    @abstractmethod
    def update_configure(self, args):
        """更新配置信息"""

    def add_config_watcher(self, standalone=False):
        try:
            config = self.download_from_nacos()
            self.update_configure(config)
            if not standalone:
                self.client.add_config_watcher(
                    data_id=self._data_id,
                    group=self._group,
                    cb=self.update_configure,
                )
        except KeyError as err:
            print_err(f"key error {err!s}")
        except nacos.NacosException as err:
            print_err(f"nacos exception {err!s}")


class NacosYamlSchemaLoader(NacosSchemaLoader):

    def download_from_nacos(self):
        config = self.client.get_config(self._data_id, self._group)
        if isinstance(config, dict):
            config_info: dict = yaml.full_load(config["raw_content"])
        else:
            config_info: dict = yaml.full_load(config)
        return config_info

    def upload_to_nacos(self, config):
        content = yaml.dump(config, allow_unicode=True, sort_keys=False)
        self.client.publish_config(
            self._data_id, self._group, content, config_type="yaml"
        )

    def update_configure(self, args):
        """更新配置信息"""
        try:
            if isinstance(args, dict):
                config_info: dict = yaml.full_load(args["raw_content"])
            else:
                config_info: dict = yaml.full_load(args)
            for key, value in config_info.items():
                if isinstance(value, dict):
                    setattr(self, key, Dict2Object(value))
                else:
                    setattr(self, key, value)
        except TypeError as err:
            print_err(f"type error: {err!s}")
        except yaml.YAMLError as err:
            print_err(f"yaml error: {err!s}")
        except AttributeError as err:
            print_err(f"attribute error: {err!s}")
        except Exception as err:
            print_err(f"unknown error: {err!s}")


class NacosJsonSchemaLoader(NacosSchemaLoader):

    def resolve_property(self, property: dict) -> dict:
        """TODO: 解析属性"""

    def download_from_nacos(self):
        config = self.client.get_config(self._data_id, self._group)
        if isinstance(config, dict):
            config_info: dict = yaml.full_load(config["raw_content"])
        else:
            config_info: dict = yaml.full_load(config)
        return config_info

    def upload_to_nacos(self, config):
        content = json.dumps(config, ensure_ascii=False, sort_keys=False, indent=4)
        self.client.publish_config(
            self._data_id, self._group, content, config_type="json"
        )

    def update_configure(self, args):
        """更新配置信息"""
        try:
            if isinstance(args, dict):
                config_info: dict = self.resolve_property(args["raw_content"])
            else:
                config_info: dict = self.resolve_property(args)
            for key, value in config_info.items():
                if isinstance(value, dict):
                    setattr(self, key, Dict2Object(value))
                else:
                    setattr(self, key, value)
        except TypeError as err:
            print_err(f"type error: {err!s}")
        except json.JSONDecodeError as err:
            print_err(f"json error: {err!s}")
        except AttributeError as err:
            print_err(f"attribute error: {err!s}")
        except Exception as err:
            print_err(f"unknown error: {err!s}")
