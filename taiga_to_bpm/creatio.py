# Standard Library
import json
from typing import List

# Third Party Stuff
import requests

from .creatio_constants import ODATA_version


class Creatio:
    def __init__(self, creatio_host, login, password, odata_version):
        self.creatio_url = creatio_host
        self.odata_version = odata_version
        self.odata_service_link = self.creatio_url + odata_version.value["service_path"]
        self.headers = odata_version.value["headers"]
        done, text = self.forms_auth(login, password)
        if done:
            self.headers["BPMCSRF"] = text["BPMCSRF"]
            self.cookies = text
        else:
            raise Exception(text)

    def forms_auth(self, login, password):
        """Аутентификация ODATA"""
        url = f"{self.creatio_url}/ServiceModel/AuthService.svc/Login"
        dict_data = {
            "UserName": login,
            "UserPassword": password,
        }
        json_data = json.dumps(dict_data)
        response = requests.post(url=url, headers=self.headers, data=json_data)

        response_data = response.json()
        if response_data["Code"] == 0:
            return True, response.cookies
        else:
            return False, response_data["Message"]

    def create_object(self, object_name: str, data: dict) -> dict | None:
        """CREATE запрос в Creatio"""
        if self.odata_version == ODATA_version.v3:
            url = self.odata_service_link + f"/{object_name}Collection"
        else:
            url = self.odata_service_link + f"/{object_name}"
        json_data = json.dumps(data)
        response = requests.post(
            url=url,
            headers=self.headers,
            data=json_data,
            cookies=self.cookies,
        )
        try:
            if self.odata_version == ODATA_version.v3:
                try:
                    object = json.loads(response.content)["d"]
                except KeyError:
                    return None
            else:
                object = json.loads(response.content)
        except Exception as exc:
            object = {
                "error": exc,
                "response": response.content,
                "url": url,
                "headers": self.headers,
                "data": data,
                # "cookies": self.cookies,
                "ODATA_version": self.odata_version,
                "HTTP_status_code": response.status_code,
            }

        return object

    def delete_object(self, object_name: str, object_id: str) -> requests.Response:
        """DELETE запрос к Creatio"""
        match self.odata_version:
            case ODATA_version.v3:
                url = (
                    self.odata_service_link
                    + f"/{object_name}Collection(guid'{object_id}')"
                )
            case ODATA_version.v4 | ODATA_version.v4core:
                url = self.odata_service_link + f"/{object_name}({object_id})"
            case _:
                raise Exception(f"ODATA version is not supported: {self.odata_version}")

        response = requests.delete(
            url=url,
            headers=self.headers,
            cookies=self.cookies,
        )
        return response

    def get_object_collection(
        self, object_name: str, parameters: List[str] = []
    ) -> List:
        _params: str = ""
        for parameter in parameters:
            _params += f"?${parameter}"

        match self.odata_version:
            case ODATA_version.v3:
                url = self.odata_service_link + f"/{object_name}Collection{_params}"
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    cookies=self.cookies,
                )
                result = json.loads(response.content)["d"]["results"]
            case ODATA_version.v4 | ODATA_version.v4core:
                url = self.odata_service_link + f"/{object_name}{_params}"
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    cookies=self.cookies,
                )
                result = json.loads(response.content)["value"]
            case _:
                result = [None]
        return result

    def get_object_by_id(self, object_name: str, object_id: str):
        match self.odata_version:
            case ODATA_version.v3:
                url = (
                    self.odata_service_link
                    + f"/{object_name}Collection(guid'{object_id}')"
                )
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    cookies=self.cookies,
                )
                result = json.loads(response.content)["d"]
            case ODATA_version.v4 | ODATA_version.v4core:
                url = self.odata_service_link + f"/{object_name}({object_id})"
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    cookies=self.cookies,
                )
                result = json.loads(response.content)
            case _:
                result = None
        return result

    # Typical implementations

    def get_contact_by_id(self, contact_id: str) -> dict | None:
        """
        Get contact object (dict type) by Id column
        """
        return self.get_object_by_id(object_name="Contact", object_id=contact_id)

    def get_creatio_contact_id(
        self, creatio_channel_id: str, number: str
    ) -> str | None:
        """
        Get contactId by phone number or other communication option
        """
        parameters = []
        match self.odata_version:
            case ODATA_version.v3:
                parameters = [
                    (
                        f"filter=CommunicationType/Id eq guid'{creatio_channel_id}' and"
                        f" Number eq '{number}'"
                    )
                ]
            case ODATA_version.v4 | ODATA_version.v4core:
                parameters = [
                    f"filter=CommunicationType/Id "
                    f"eq {creatio_channel_id} and Number eq '{number}'"
                ]
        result = self.get_object_collection(
            object_name="ContactCommunication",
            parameters=parameters,
        )[0]
        if result is None:
            return None
        else:
            return result["ContactId"]

    def post_receipt(self, board_creatio_id):
        """Создать экземпляр SLReceipt  в Creatio"""
        dict_data = {
            "SLTrelloDeskId": board_creatio_id,
        }
        return self.create_object("SLReceipt", dict_data)

    def create_message_log_sms(
        self,
        mobie_phone,
        text,
    ):
        dict_data = {
            "Address": mobie_phone,
            "Text": text,
            "MessageChannelId": "F7135347-9F65-4573-B409-6ADA0C47ADB6",  # SMS
        }
        return self.create_object("MessageLog", data=dict_data)

    def post_phone_book(self, full_name, lead_id, phone_number):
        dict_data = {
            "UsrFullName": full_name,
            "UsrLeadId": lead_id,
            "UsrNumber": phone_number,
        }
        return self.create_object("SLPhoneBook", dict_data)
