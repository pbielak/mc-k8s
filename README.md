# Prerequisite
1. Install minikube, kubectl (version: 1.7.8), VirtualBox.
2. Run `minikube start` and wait for cluster to be ready.

# Deploy 
1. Use `kubectl` to deploy all components (deployments, services)
`kubectl create -f filename.yaml`
2. Deploy components in following order:
* Memcached: deployment, service
* Metrics: deployment, service
* Scaler: deployment
* Mutilate: deployment (for testing purposes)
