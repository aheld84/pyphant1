<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
          "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta http-equiv="refresh" content="5; URL={{back_url}}">
  <title>Pyphant Web Interface</title>
</head>
<body onload="self.focus(); document.backform.elements[0].focus()">
  <h1>{{heading}}</h1>
  <p>
    <form action="{{back_url}}" method="GET" name="backform">
      <input type="submit" value="-- back --" tabindex="0" />
    </form>
  </p>
  <p>
    {{message}}
  </p>
  %include back url=back_url
</body>
</html>
