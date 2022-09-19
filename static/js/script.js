const btn1 = document.getElementById("btn1");
const btn5 = document.getElementById("btn5");
const btn10 = document.getElementById("btn10");

const setBtnsDisabled = (disabled) => {
  btn1.disabled = disabled;
  btn5.disabled = disabled;
  btn10.disabled = disabled;
};

const postBlink = (blink_count) => {
  return () => {
    setBtnsDisabled(true);
    const payload = {blink_count: blink_count};
  
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
      setBtnsDisabled(false);
    });
  }
};

btn1.addEventListener('click', postBlink(1));
btn5.addEventListener('click', postBlink(5));
btn10.addEventListener('click', postBlink(10));