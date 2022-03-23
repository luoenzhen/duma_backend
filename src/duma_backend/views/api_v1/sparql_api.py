import logging

import requests
from flask import Response, current_app, request

# from flask_tern import openapi
from flask_tern.auth import require_user

from .blueprint import bp


@bp.route("/sparql", methods=["GET"])
@require_user
def sparql_endpoint_get():
    """get one or more sparql query results"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling sparql_endpoint_get()\n")

    headers = dict()
    for header in request.headers:
        headers.update({header[0]: header[1]})
    # print("headers", headers)

    query = request.values.get("query")
    query_endpoint = (
        current_app.config["SPARQL_URL"]
        + current_app.config["SPARQL_REPOSITORY"]
        + current_app.config["SPARQL_REPOSITORY_KNOWLEDGE_GRAPH_CORE"]
    )

    r = requests.get(
        query_endpoint,
        auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
        headers=headers,
        params={"query": query},
    )

    response = Response(response=r.content.decode("utf-8"), status=r.status_code)
    # print("\nresponse\n", response.data)
    response.headers["content-type"] = r.headers["content-type"]
    print("\nheader\n", response.headers)
    return response


@bp.route("/sparql", methods=["POST"])
@require_user
def sparql_endpoint_post():
    """update sparql query"""
    logger = logging.getLogger(__name__)
    logger.info("\tCalling sparql_endpoint_post()\n")

    headers = dict()
    for header in request.headers:
        headers.update({header[0]: header[1]})

    # Set the parameters for a SPARQL 1.1 UPDATE query
    query = request.values.get("update")
    query_endpoint = (
        current_app.config["SPARQL_URL"]
        + current_app.config["SPARQL_REPOSITORY"]
        + current_app.config["SPARQL_REPOSITORY_KNOWLEDGE_GRAPH_CORE"]
    )
    url = (
        current_app.config["SPARQL_URL"]
        + current_app.config["SPARQL_REPOSITORY"]
        + current_app.config["SPARQL_REPOSITORY_KNOWLEDGE_GRAPH_CORE"]
        + "/statements"
    )

    data_key = "update"
    if not query:
        # Set the parameters for a SPARQL 1.1 query
        query = request.values.get("query")
        data_key = "query"
        url = query_endpoint

    r = requests.post(
        url,
        auth=(current_app.config["SPARQL_USER"], current_app.config["SPARQL_PASS"]),
        headers=headers,
        data={data_key: query},
    )

    response = Response(r.content.decode("utf-8"), status=r.status_code)
    for header in r.headers:
        # See comment in sparql_endpoint() for explanation.
        if header.lower() == "content-encoding":
            continue
        response.headers[header] = r.headers[header]

    return response
