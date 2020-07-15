import argparse
import logging
import os
import sys
from abc import abstractmethod
from pathlib import Path

from ._typing import FilePath, FilePathOrBuffer


class ArgParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(formatter_class=argparse.RawTextHelpFormatter, **kwargs)
        self.logger = logging.getLogger('Parser')

    def error(self, message: str) -> None:
        """Write an error to stderr, print help, and exit

        :param message: error message
        :return: None
        """
        sys.stderr.write(f"error: {message}\n")
        self.print_help()
        sys.exit(2)

    def parse_path(self, path: FilePath, check_exists=False) -> Path:
        """Check if a path invalid or exist

        :param path: checking path
        :param check_exists: check if the path exists
        :return: parsed path
        """
        try:
            path = Path(path)
        except Exception as e:
            self.error(f"invalid path {path}: {e}")
        if check_exists and not path.exists():
            self.error(f"path {path} does not exist")
        return path

    def parse_input_arg_value(self, input_arg_value: str, stdin_value: str = '-') -> FilePathOrBuffer:
        """Check if input arg is stdin or a file path

        :param input_arg_value:
        :param stdin_value:
        :return: parsed input arg value
        """
        return sys.stdin if input_arg_value == stdin_value else self.parse_path(input_arg_value, True)

    def parse_output_arg_value(self, output_arg_value: str, stdout_value: str = '-') -> FilePathOrBuffer:
        """Check if output arg is stdout or a file path

        :param output_arg_value:
        :param stdout_value:
        :return: parsed input arg value
        """
        return sys.stdout if output_arg_value == stdout_value else self.parse_path(output_arg_value)

    def parse_env_variable(self, var_name, must_exist: bool = False):
        """Get an environment variable

        :param var_name: name of the environment variable
        :param must_exist: if must exist and environemnt not found then call erorr else warning
        :return:
        """
        env_var = os.getenv(var_name)
        if not env_var:
            if must_exist:
                self.error(f"environment variable {env_var} does not exist")
            else:
                self.logger.warning(f"environment variable {env_var} does not exist")
        return env_var

    @staticmethod
    def prompt_confirmation(message: str, default: bool = None) -> bool:
        """Prompt confirmation message

        :param message: confirmation message
        :param default: default prompt value
        :return:
        """
        valid_responses = {
            'yes': True,
            'y': True,
            'no': False,
            'n': False
        }
        if default is None:
            prompt = '[y/n]'
        elif default:
            prompt = '[Y/n]'
        else:
            prompt = '[y/N]'
        while True:
            sys.stdout.write(f"{message} {prompt}")
            response = input().lower()
            if default is not None and response == '':
                return default
            elif response in valid_responses:
                return valid_responses[response]
            else:
                sys.stdout.write("Please respond with yes(y) or no(n)'\n")


class ParserWrapper:
    def __init__(self, add_help=True):
        if add_help:
            self.parser = ArgParser()
        else:
            self.parser = ArgParser(add_help=False)

    @abstractmethod
    def parse_and_execute(self, parsing_args):
        pass
