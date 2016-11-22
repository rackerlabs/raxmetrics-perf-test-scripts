
import os.path

import java.lang.System
import java.io.File
import java.io.FileInputStream
import java.util.Properties

from org.jasypt.properties import EncryptableProperties
from org.jasypt.encryption.pbe import StandardPBEStringEncryptor

from user import User
from config import clean_configs
import py_java


def get_user(config, grinder):
    """Load user credentials from the provided config.

    The algorithm proceeds as follows:

    First, the config is checked for the `auth_url`, `auth_username`, and
    `auth_api_key` properties. If those are provided, then a `user.User` object
    is constructed and returned.

    If any of those properties is not provided in the main configuration file,
    then the `auth_properties_path` property is checked. If that is not
    provided, processing stops and `None` is returned. Otherwise, the
    `auth_properties_path` property is interpreted as the relative path to a
    second properties file.

    Similar to the above, the second properties file will be checked for the
    `auth_url`, `auth_username`, and `auth_api_key` properties. If those are
    provided, then a `user.User` object is constructed and returned. If any of those
    properties is not provided, then `None` is returned.

    No attempt is made to authenticate the user based on the provided
    properties. Authentication will occur lazily the calling code tries to
    access the `User`'s token or tenant data. If the credentials are incorrect,
    an error will occur then, rather than in this function.

    Any exceptions (e.g. `IOError("File not found")` ) are propagated to the
    caller.

    :param config: the test configuration loaded from the .properties file(s)
    :param grinder: the ScriptContext provided by The Grinder, used to resolve
        file paths

    :return: a user.User object for the configured user credentials, or None if
        any credential properties weren't provided in the config.
    :rtype: user.User
    """
    auth_url = config.get('auth_url', None)
    auth_username = config.get('auth_username', None)
    auth_api_key = config.get('auth_api_key', None)
    if auth_url and auth_username and auth_api_key:
        return User(auth_url, auth_username, auth_api_key)

    auth_properties_encr_key_file = config.get('auth_properties_encr_key_file',
                                               None)
    encryptor = None
    if auth_properties_encr_key_file:
        auth_properties_encr_key_file = os.path.expanduser(
            auth_properties_encr_key_file)
        stream = java.io.FileInputStream(auth_properties_encr_key_file)
        auth_props_encr_key_props = java.util.Properties()
        auth_props_encr_key_props.load(stream)
        auth_props_encr_key_dict = py_java.dict_from_properties(
            auth_props_encr_key_props)
        auth_props_encr_key = auth_props_encr_key_dict.get('password', None)
        encryptor = StandardPBEStringEncryptor()
        encryptor.setPassword(auth_props_encr_key)

    user_creds_relative_path = config.get('auth_properties_path', None)
    if user_creds_relative_path:
        user_creds_relative = java.io.File(user_creds_relative_path)
        user_creds_file = grinder.getProperties().resolveRelativeFile(user_creds_relative)
        stream = java.io.FileInputStream(user_creds_file)
        if encryptor:
            user_creds_props = EncryptableProperties(encryptor)
        else:
            user_creds_props = java.util.Properties()
        user_creds_props.load(stream)
        user_creds_dict = clean_configs(py_java.dict_from_properties(user_creds_props))
        auth_url = user_creds_dict.get('auth_url', None)
        auth_username = user_creds_dict.get('auth_username', None)
        auth_api_key = user_creds_dict.get('auth_api_key', None)
        if auth_url and auth_username and auth_api_key:
            return User(auth_url, auth_username, auth_api_key)
    return None