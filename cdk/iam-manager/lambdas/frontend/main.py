


def handler(event, context): 
    switcher_call = "https://xxx"
    learner_call = "https://yyy"
    html_body = f"""<html>
<body>

<h2>Grant Learning Rights</h2>

<form action="{switcher_call}">
  <label for="fname">Role/User ARN:</label><br>
  <input type="text" id="arn" name="arn" value=""><br><br>

  <input type="submit" value="Submit">
</form> 

<p>If you click the "Submit" button, that role will be assigned administrative rights for the period of learning.</p>
<hr>
<h2>Learn new access</h2>

<form action="{learner_call}">
  <label for="fname">Role/User ARN:</label><br>
  <input type="text" id="arn" name="arn" value=""><br><br>

  <input type="submit" value="Submit">
</form> 

<p>If you click the "Submit" button, this role will be updated with new righs.</p>

</body>
</html>
"""

    return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain'
            },
            'body': html_body
    }