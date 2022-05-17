from icecream import ic
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response:
        errors = []
        items = dict(response.data.items())
        for k, v in items.items():
            errors.append({k: response.data.pop(k)})
        response.data["errors"] = []
        for error in errors:
            if error.get("detail", None):
                response.data["errors"].append(
                    {
                        "code": error.get("detail").code.upper(),
                        "message": f"{str(error.get('detail'))}",
                    }
                )
                return response

            for field, er in error.items():
                code = ""
                msg = ""
                if isinstance(er, dict):
                    for f, err in er.items():
                        for i in err:
                            code = i.code.upper()
                            msg = err

                else:
                    for i in er:
                        code = i.code.upper()
                        msg = er
                response.data["errors"].append(
                    {"code": code, "path": field, "message": "".join(msg)}
                )
    return response
