import os

if os.environ["DEPLOYMENT_ENV"]=="AWS":
    redirect_uri="https://vsmt-setchks-app-test-lb.k8s-nonprod.texasplatform.uk/cognito_test"
else:
    redirect_uri="http://localhost:5000/cognito_test"