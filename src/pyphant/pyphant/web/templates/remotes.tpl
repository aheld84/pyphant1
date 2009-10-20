%include htmlhead
<body>
  <h1>Manage Remotes</h1>
  %include back url='/'
  <p>
    The following table shows the remote knowledge nodes that are
    connected to the local knowledge node.
  </p>
  <p>
    <form action="/remote_action" method="GET">
      <input type="hidden" name="action" value="add" />
      <table border="0">
        <tr>
          <td>
            <input type="text" name="host" value="host"
                   size="30" maxlength="500" />
          </td>
          <td>
            <input type="text" name="port" value="port" size="5"
                   maxlength="5" />
          </td>
          <td>
            <input type="submit" value="add" />
          </td>
        </tr>
      </table>
    </form>
    {{remote_table}}
  </p>
  <p>
  %include back url='/'
</body>
</html>
