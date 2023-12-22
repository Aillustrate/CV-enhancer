from datetime import datetime, timedelta

import requests


class YandexIAMClient:
    """
    YandexIAMClient class for managing Yandex Identity and Access Management tokens.

    Args:
        oauth_token (str): Yandex Passport OAuth token for authentication.

    Attributes:
        base_url (str): Base URL for Yandex IAM API.
        tokens_url (str): URL for obtaining IAM tokens.
        headers (dict): HTTP headers for requests.
        oauth_token (str): Yandex Passport OAuth token.
        last_request_time (datetime): Timestamp of the last token request.
        iam_token (str): Current IAM token.

    Methods:
        _is_token_expired(): Check if the current IAM token has expired.
        _refresh_token_if_expired(): Refresh the IAM token if it has expired.
        get_key(): Get the current IAM token.
        _get_new_token(): Request a new IAM token using the provided OAuth token.
    """

    def __init__(self, oauth_token):
        """
        Initialize the YandexIAMClient.

        Args:
            oauth_token (str): Yandex Passport OAuth token for authentication.
        """
        self.base_url = "https://iam.api.cloud.yandex.net/iam/v1"
        self.tokens_url = f"{self.base_url}/tokens"
        self.headers = {"Content-Type": "application/json"}
        self.oauth_token = oauth_token
        self.last_request_time = None
        self.iam_token = ""

    def _is_token_expired(self) -> bool:
        """
        Check if the current IAM token has expired.

        Returns:
            bool: True if the token has expired, False otherwise.
        """
        if self.last_request_time is None:
            return True
        elapsed_time = datetime.now() - self.last_request_time
        return elapsed_time > timedelta(hours=10)

    def _refresh_token_if_expired(self) -> None:
        """
        Refresh the IAM token if it has expired.
        """
        if self._is_token_expired():
            self._get_new_token()

    def get_key(self) -> str:
        """
        Get the current IAM token.

        Returns:
            str: Current IAM token.
        """
        self._refresh_token_if_expired()
        return self.iam_token

    def _get_new_token(self) -> None:
        """
        Request a new IAM token using the provided OAuth token.

        Raises:
            Exception: If the request for a new token fails.
        """
        data = {"yandexPassportOauthToken": self.oauth_token}
        response = requests.post(self.tokens_url, json=data, headers=self.headers)
        self.last_request_time = datetime.now()

        if response.status_code == 200:
            self.iam_token = response.json()["iamToken"]
        else:
            raise Exception(
                f"Failed to get new token. Status code: {response.status_code}, Response: {response.text}"
            )


class YandexTranslateClient:
    """
    YandexTranslateClient provides a simple interface for translating text using the Yandex Translate API.

    Args:
        folder_id (str): The folder ID for the Yandex Cloud Translation service.
        target_language (str): The target language code for translation.

    Attributes:
        folder_id (str): The folder ID for the Yandex Cloud Translation service.
        target_language (str): The target language code for translation.
        base_url (str): The base URL for the Yandex Translate API.

    Methods:
        translate_text(texts: Union[str, List[str]], iam_token: str) -> str:
            Translate the given text(s) to the target language.

    Example:
        client = YandexTranslateClient(folder_id="your_folder_id", target_language="en")
        iam_token = "your_iam_token"
        translated_text = client.translate_text("Привет, мир!", iam_token)
        print(translated_text)
    """

    def __init__(self, folder_id, target_language):
        """
        Initialize YandexTranslateClient with folder ID and target language.

        Args:
            folder_id (str): The folder ID for the Yandex Cloud Translation service.
            target_language (str): The target language code for translation.
        """
        self.folder_id = folder_id
        self.target_language = target_language
        self.base_url = "https://translate.api.cloud.yandex.net/translate/v2/translate"

    def translate_text(self, texts, iam_token) -> str:
        """
        Translate the given text(s) to the target language.

        Args:
            texts (Union[str, List[str]]): The text or list of texts to be translated.
            iam_token (str): The IAM token for authentication.

        Returns:
            str: The translated text.
        """
        body = {
            "targetLanguageCode": self.target_language,
            "texts": texts if isinstance(texts, list) else [texts],
            "folderId": self.folder_id,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {iam_token}",
        }

        response = requests.post(self.base_url, json=body, headers=headers)
        translated_text = response.json()["translations"][0]["text"]
        return translated_text
