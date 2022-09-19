const btn = document.getElementById("btn");

const postBlink = () => {
  btn.disabled = true;
  console.log("blink");

  const payload = {blink_count: 5};

  fetch("/api/led", {
    method: "POST",
    headers: {'Content-Type': 'application/json'}, 
    body: JSON.stringify(payload)
  }).then(
    res => {
    res.text().then(data => {
      console.log(data);
      alert(data);
    }).catch(err => {
      console.error(err);
      alert(err);
    })
  }).catch(err => {
    console.error(err);
    alert(err);
  }).finally(() => {
    btn.disabled = false;
  });
};

btn.addEventListener('click', postBlink);