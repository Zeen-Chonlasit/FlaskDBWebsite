function getProducTable() {
  var form_data = new FormData();
  form_data.append("page", $("#page").val());

  $.ajax({
    type: "POST",
    url: "/product/select/ajax",
    data: form_data,
    contentType: false,
    cache: false,
    processData: false,
    success: function (data) {
      $("#tabledata").html(data);
    },
  });
}

function genPDF(){
    var t = $('#t').val()
    var doc = new jsPDF()

    doc.text(t, 10, 10)
    doc.save('a4.pdf')
}

function readURL(input) {
  if (input.prop("files") && input.prop("files")[0]) {
    alert("test");
    var reader = new FileReader();

    reader.onload = function (e) {
      $("#imagepreview").attr("src", e.target.result).width(150).height(200);
    };

    reader.readAsDataURL(input.prop("files")[0]);
  }
}

function init() {
  //ผูก event เมื่ออัพโหลดไฟล์เสร็จ ให้เรียกฟังชัน upload_file()
  $("#uploadfile").bind("change", function () {
    readURL($("#uploadfile"));
  });
}

function customerall() {
  var form_data = new FormData();
  form_data.append("page", $("#page").val());

  $.ajax({
    type: "POST",
    url: "/customer/all",
    data: form_data,
    contentType: false,
    cache: false,
    processData: false,
    success: function (data) {
      $("#tabledata").html(data);
    },
  });
}

//เมื่อโหลดpage เสร็จให้เรียกฟังชัน init()
$(document).ready(function () {
  init();
});



