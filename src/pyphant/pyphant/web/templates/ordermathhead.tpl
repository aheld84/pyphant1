<?xml version="1.0"?>
<!DOCTYPE html    PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN"
           "http://www.w3.org/Math/DTD/mathml2/xhtml-math11-f.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
  <title>Pyphant Web Interface</title>
  <script type="text/javascript" src="/script/LaTeXMathML.js"></script>
  <script type="text/javascript">
    function set_order_by(order_by_value) {
      if (document.search_form.order_by.value == order_by_value) {
        if (document.search_form.order_asc.value == "True") {
          document.search_form.order_asc.value = "False";
        } else {
          document.search_form.order_asc.value = "True";
        }
      } else {
        document.search_form.order_by.value = order_by_value;
      }
      document.search_form.jump.value = "True";
      document.search_form.submit();
    }
    function set_offset(offset_value) {
      document.search_form.offset.value = offset_value;
      document.search_form.jump.value = "True";
      document.search_form.submit();
    }
    function add_attribute() {
      document.search_form.add_attr.value = "True";
      document.search_form.submit();
    }
    function remove_attribute(apost) {
      document.search_form.rem_attr.value = apost;
      document.search_form.submit();
    }
  </script>
</head>
