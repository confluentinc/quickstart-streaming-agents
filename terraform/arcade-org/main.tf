resource "confluent_invitation" "arcade_user" {
  for_each  = var.user_emails
  email     = each.value
  auth_type = "AUTH_TYPE_LOCAL"
}
