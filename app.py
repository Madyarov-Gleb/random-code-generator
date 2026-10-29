import secrets

from flask import Flask, render_template


def generate_code() -> str:
    return f"{secrets.randbelow(9000) + 1000:04d}"


def create_app(test_config: dict | None = None) -> Flask:
    application = Flask(__name__)

    if test_config is not None:
        application.config.update(test_config)

    @application.after_request
    def disable_cache(response):
        response.headers["Cache-Control"] = "no-store"
        return response

    @application.get("/")
    def code():
        return render_template("code.html", code=generate_code())

    return application


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
