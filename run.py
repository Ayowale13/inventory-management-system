"""Application entry point."""
from app import create_app, db
from app.models import User, Product, Sale, Restock, CustomField, ProductCustomValue, ActivityLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db, User=User, Product=Product, Sale=Sale,
        Restock=Restock, CustomField=CustomField,
        ProductCustomValue=ProductCustomValue, ActivityLog=ActivityLog,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
