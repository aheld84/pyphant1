<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
          "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>Pyphant Web Interface</title>
</head>
<body>
  <h1>Pyphant Web Interface</h1>
  <p>
    <img src="/images/pyphant.png" alt="pyphant-logo" width="300" height="100">
  </p>
  <h2>Local Knowledge Manager</h2>
  <p>
    The local knowledge manager '{{local_uuid}}'
    is bound to a knowledge node which provides this web interface.
    The knowledge node is listening at {{local_url}} for requests.
  </p>
  <h2>Remote Knowledge Nodes</h2>
  <p>
    The following table shows the remote knowledge nodes that are
    connected to the local knowledge node.
  </p>
  {{remote_table}}
</body>
</html>
