resource "aws_lambda_function" "analyze_with_llm" {
    function_name = "analyze-with-llm"
    role = aws_iam_role.analyze_with_llm_role.arn
    handler = "app.lambda_handler"
    runtime = "python3.10"
    filename = "analyze-with-llm.zip"
}
