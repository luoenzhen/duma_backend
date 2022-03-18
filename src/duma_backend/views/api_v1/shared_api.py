import logging

import requests
from flask import current_app, json, jsonify, request
from flask_tern import openapi
from flask_tern.auth import require_user
from flask_tern.auth.oidc import oauth

from .blueprint import bp

# SUBMIT_FLAG = "?submitted=false"
UPDATE_FLAG = "/update/"

# from shared APIs
@bp.route("/shared/document", methods=["GET"])
@require_user
@openapi.validate()
def from_shared_get():
    """get all the vocabularies of from shared"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling from_shared_get()\n")

    metadata = oauth.oidc.load_server_metadata()
    sharedResultList = []
    with oauth.oidc._get_oauth_client(**metadata) as client:
        # check our current is recent enough otherwise renew
        client.token = oauth.oidc.token
        logger.info("\tChecking access token...\n")
        if client.token:
            logger.info("\tClient has access token\n")
            queryUrl = current_app.config["SHARED_URL"] + (
                current_app.config["SHARED_SUBMIT_FLAG"] if "SHARED_SUBMIT_FLAG" in current_app.config else ""
            )
            logger.info("\tquery from %s\n", queryUrl)
            fromShared = client.get(queryUrl).json()
            if len(fromShared["results"]):
                logger.info("\tFound %s records from SHaRED\n", len(fromShared["results"]))
                for result in fromShared["results"]:
                    sharedResultDict = {}
                    resultUrl = result["url"]
                    logger.info("\tresultUrl %s\n", resultUrl)
                    if client.get(resultUrl) and client.get(resultUrl).json():
                        submittedData = client.get(resultUrl).json()
                        sharedResultDict["uuid"] = result["uuid"]
                        sharedResultDict["data"] = submittedData
                        sharedResultList.append(sharedResultDict)
            else:
                logger.info("\tFound NO records from SHaRED\n")
        else:
            logger.warning("\t!!Client has NO access token!!\n")
    return jsonify(sharedResultList)


@bp.route("/shared/document/<uuid>", methods=["GET"])
@require_user
@openapi.validate()
def from_shared_id_get(uuid: str):
    """show the from shared record with that id"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling from_shared_id_get(id)\n")

    fromShared = []
    # Sample data
    # fromShared = [
    #     {
    #         "serial": "d",
    #         "isUserDefined": True,
    #         "userAddedCategory": "instrument",
    #         "label": "User-added instrument",
    #         "uri": "93455905-204c-4bb3-9f75-e964fbb8b13c",
    #         "description": "debugging",
    #         "source": "asdf",
    #         "duma_path": ".identificationInfo.keywordsInstrument.keywords.0",
    #         "url": "https://shared-dev.tern.org.au/api/duma/eab088a6-7b2c-4c42-bf2c-c45a712cdd5e/?submitted=false",
    #     }
    # ]
    metadata = oauth.oidc.load_server_metadata()
    with oauth.oidc._get_oauth_client(**metadata) as client:
        # check our current is recent enough otherwise renew
        client.token = oauth.oidc.token
        logger.info("\tChecking access token...\n")
        if client.token:
            logger.info("\tClient has access token\n")
            queryUrl = (
                current_app.config["SHARED_URL"]
                + uuid
                + (current_app.config["SHARED_SUBMIT_FLAG"] if "SHARED_SUBMIT_FLAG" in current_app.config else "")
            )
            logger.info("\tquery from %s\n", queryUrl)
            fromShared = client.get(queryUrl).json()
    return jsonify(fromShared)


@bp.route("/shared/document", methods=["PUT"])
@require_user
@openapi.validate()
def from_shared_id_put():
    """update from shared record"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling from_shared_id_put()\n")

    metadata = oauth.oidc.load_server_metadata()
    response = json.dumps({})
    with oauth.oidc._get_oauth_client(**metadata) as client:
        # check our current is recent enough otherwise renew
        client.token = oauth.oidc.token
        logger.info("\tChecking access token...\n")
        # logger.info("\ttoken is %s\n", client.token)
        if client.token:
            headers = {"Authorization": "Bearer " + client.token["access_token"], "Content-Type": "application/json"}
            logger.info("\tClient has access token\n")
            request_data = request.get_json()["data"]
            # print("request_data", request_data)
            url = request_data["url"]
            logger.info("\tPosting to %s\n", url)
            response = requests.put(url, data=json.dumps(request_data), headers=headers)
            # print(response.json())
    return response.json()


@bp.route("/shared/document", methods=["POST"])
@require_user
@openapi.validate()
def from_shared_id_post():
    """update from shared record"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling from_shared_id_post()\n")
    return from_shared_id_put()
