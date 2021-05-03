import webapp2


class SendMessageHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get["gameName"]
        '''
        email = self.request.get["email"]
        details = self.request.get["details"]
        message = mail.EmailMessage(
            sender="yourauthorized@sender.com",
            subject=str(name) + " has submitted a proposal.")

        message.to = "Your Name <your@email.com>"
        message.body = "Name:\n" + str(name) + "\n\nEmail:\n" + str(email) + "\n\nDetails:\n" + str(details)

        message.send()
        '''


app = webapp2.WSGIApplication([('/gameSpecs', SendMessageHandler),], debug=True)