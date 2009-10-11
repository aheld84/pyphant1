<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
          "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>Pyphant Web Interface &#64; {{local_url}}</title>
</head>
<body>
  <h1>Pyphant Web Interface &#64; {{local_url}}</h1>
  <p>
    <img src="/images/pyphant.png" alt="pyphant-logo"
         width="300" height="100">
  </p>
  <h2>Remote Knowledge Nodes</h2>
  <p>
    The following table shows the remote knowledge nodes that are
    connected to the local knowledge node. The uuid of the local knowledge
    node is '{{local_uuid}}'.
  </p>
  {{remote_table}}
</body>
</html>
