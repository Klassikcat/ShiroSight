<div align="center">
  <img src="./static/shirosight_logo.png" alt="shirosight-logo" width="300" height="300"><br />
  <img src="./static/shirosight-logo.svg" alt="shirosight" width="650" height="200">
</div>
<div align="center">
<b>
<a href="docs/installation.md">Installation</a> | <a href="docs/configuration.md">Configuration</a> | <a href="docs/usage.md">Usage</a> | <a href="docs/examples.md">Example</a> | <a href="docs/contributing.md">Contributing</a>
</b>
</div>
<br>
<hr>

Cloudwatch sucks. Solve it with ShiroSight.

ShiroSight is an open-source tool for log analysis powered by Large Language Models. It leverages serverless functions and workflows (both Argo workflow for k8s and Step functions for AWS and non-k8s environments) to process and analyze logs using models from providers like OpenAI, Claude, and others. ShiroSight helps teams extract meaningful insights from their log data without the need for complex infrastructure management and tons of **QUERY**".

# Key Feature

- Deep integration with Cloudwatch and Athena

# Installation

For quick deployment, follow these steps:

```bash
aws sso login
cd deployments/terraform
terraform init
terraform apply 
```

Or, see [Installation](./docs/installation.md) to get more information

# License

