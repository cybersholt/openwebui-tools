from google_tools import Tools

tools = Tools()

if __name__ == '__main__':
    # out = tools.get_email_content("194fa5b21343aeb4")
    out = tools.get_user_emails(4)
    # out = tools.get_user_events(4)
    # print(out)

