import os
# from flask import current_app

if os.environ["DEPLOYMENT_ENV"]=="AWS":
    # redirect_uri="https://vsmt-setchks-app-test-lb.k8s-nonprod.texasplatform.uk/cognito_test"
    # redirect_uri=f"https://vsmt-setchks-app-{os.environ['DEPLOYMENT_AWSENV']}-lb.k8s-nonprod.texasplatform.uk/cognito_test"
    # redirect_uri=f"https://vsmt-setchks-app-{current_app.config['ENVIRONMENT']}-lb.k8s-nonprod.texasplatform.uk/cognito_test"
    redirect_uri=f"https://vsmt-setchks-app-{os.environ['ENV']}-lb.k8s-nonprod.texasplatform.uk/cognito_test"
else:
    redirect_uri="http://localhost:5000/cognito_test"