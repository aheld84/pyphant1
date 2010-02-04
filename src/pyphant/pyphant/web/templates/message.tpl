%include htmlhead
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
