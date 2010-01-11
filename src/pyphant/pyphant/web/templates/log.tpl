%include htmlhead
<body>
  <h1>Pyphant Log for {{url}}</h1>
  %include back url='/'
  <p>
    <pre>
{{loglines}}
    </pre>
  </p>
  %include back url='/'
</body>
</html>
