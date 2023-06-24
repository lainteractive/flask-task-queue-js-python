function ai(prompt) {
  return new Promise((resolve, reject) => {
    fetch("/start_ai", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt })
    })
    .then(response => response.json())
    .then(data => {
      let taskStatus = "PENDING";
      const { task_id } = data;
      const interval = setInterval(() => {
        fetch(`/task_status/${task_id}`)
        .then(response => response.json())
        .then(statusData => {
          taskStatus = statusData.state;   
          console.log("Task status:", taskStatus);
          if (taskStatus !== "PENDING") {
            clearInterval(interval);
            if (taskStatus === "SUCCESS") {
              const result = statusData.result;
              console.log("Task result:", result);
              resolve(result);
            } else {
              resolve("Task failed.");
              reject(new Error(`Task failed with status ${taskStatus}`));
            }
          }
        })
        .catch(error => {
          clearInterval(interval);
          console.error(error);
          reject(error);
        });
      }, 1000);
    })
    .catch(error => {
      console.error(error);
      reject(error);
    });
  });
}
