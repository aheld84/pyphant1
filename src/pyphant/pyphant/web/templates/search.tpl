%include ordermathhead
<body{{body_onload}}>
  <h1>Browse Data Containers</h1>
  %include back url='/'
  <hr />
  <form method="GET" action="/search" name="search_form">
    <input type="hidden" name="order_by" value="{{order_by}}" />
    <input type="hidden" name="order_asc" value="{{order_asc}}" />
    <input type="hidden" name="jump" value="False" />
    <p>
{{common}}
      <br />
{{date}}
    </p>
    <input type="submit" value=" update " />
    <hr />
    <input type="checkbox" name="shorten" value="True"
           onchange="document.search_form.submit();"
           {{shorten}} />shorten values<br />
    <a name="result_view"><p>
{{result}}
    </p></a>
  </form>
  <hr />
  %include back url='/'
</body>
</html>
