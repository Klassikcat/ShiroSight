resource "aws_iam_role" "analyze_with_llm_role" {
    name = "analyze-with-llm-role"
    assume_role_policy = file("assume-role-policy.json")
}


resource "aws_iam_role_policy_attachment" "analyze_with_llm_policy_attachment" {
    role = aws_iam_role.analyze_with_llm_role.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}