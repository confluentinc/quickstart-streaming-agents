output "user_ids" {
  description = "Map of email to Confluent Cloud user ID"
  value = {
    for email, invitation in confluent_invitation.arcade_user :
    email => invitation.user
  }
}

output "invitation_ids" {
  description = "Map of email to invitation ID"
  value = {
    for email, invitation in confluent_invitation.arcade_user :
    email => invitation.id
  }
}
