document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector("#compose-form").addEventListener('submit', send_email);

  // By default, load the inboxs
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-details-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#body-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function view_email(id) {
  fetch(`/emails/${id}`)
  .then(responce => responce.json())
  .then(email => {

    // Hide the other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-details-view').style.display = 'block';
    document.querySelector('#body-view').style.display = 'block';
    
    // Create the email details 
    document.querySelector('#email-details-view').innerHTML = `
    <b>From: </b>${email.sender}<br>
    <b>To: </b>${email.recipients}<br>
    <b>Subject: </b>${email.subject}<br>
    <b>Timestamp: </b>${email.timestamp}<br>
    `;
 
    // Create a reply button to reply with the email
    const reply = document.createElement('button');
    reply.className = "btn btn-sm btn-outline-primary m-1 mt-2"
    reply.innerHTML = "Reply";

    // If the reply button is clicked, compose a new email
    reply.addEventListener('click', () => {
      compose_email();

      // Automatically make the sender the new recipient
      document.querySelector('#compose-recipients').value = email.sender;
      
      // Make the subject. If it does not have Re:, put it. Used the split fuction to determine
      let subject = email.subject;
      if (subject.split(" ", 1)[0] != "Re:") {
        subject = "Re: " + subject;
      }
      document.querySelector('#compose-subject').value = subject;
      let text = email.body.replace(/(<([^>]+)>)/gi, '');
      let body = `On ${email.timestamp} ${email.sender} wrote: ${text}
      `;
      document.querySelector('#compose-body').value = body;

    });

    // Append the reply button to email-details-view
    document.querySelector('#email-details-view').appendChild(reply);
    
    // Make the archive button
    archive = document.createElement('button');
    // If it is not archived, put Archive, Unarchive otherwise
    archive.innerHTML = !email.archived ? 'Archive': 'Unarchive';
    archive.className = "btn btn-sm btn-outline-primary m-1 mt-2"
    archive.addEventListener('click', () => {
      fetch('/emails/' + email.id, {
        method: 'PUT',
        body: JSON.stringify({ 
          archived : !email.archived
        })
      })
      .then(response => load_mailbox('inbox'))
    });
    // Append the archive button
    document.querySelector('#email-details-view').appendChild(archive);

    document.querySelector('#body-view').innerHTML = `
    <hr>
    <div class="container">${email.body}<div>
    `
        
    // If the email is not read, make it read 
    if (!email.read) {
      fetch('/emails/' + email.id, {
        method: 'PUT',
        body: JSON.stringify({ read: true })
      })
    }
  })
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-details-view').style.display = 'none';
  document.querySelector('#body-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
 
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

      // Check if there are any emails to display
      if (emails.length === 0) {
        const element = document.createElement('div');
        element.innerHTML = 'No available mail.';
        document.querySelector('#emails-view').appendChild(element);
      } else {

        // Loop emails and create a div 
        emails.forEach(email => {
          const element = document.createElement('div');
          element.className = email.read ? "email-div read": "email-div unread";

          element.innerHTML = `
          <div id="sender"><b>${email.sender}</b></div>
          <div id="subject">${email.subject}</div>
          <div id="timestamp">${email.timestamp}</div>
          `;

          element.addEventListener('click', () => view_email(email.id));

          document.querySelector('#emails-view').append(element);
        });
      }
  });
}


function send_email(event) {
  // Prevent to go to inbox by default
  event.preventDefault();
  
  // Assign the values in variables
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Use the fetch function
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.error) {
      // If an error occurred, show an alert
      alert(result.error);
    } else {
      // Direct to the sent section
      load_mailbox('sent');
    }
  })
  .catch(error => {
    // If there is a network error, show an alert
    alert("Unable to send email. Please check your network connection.");
  });
}


