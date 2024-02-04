import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import frappe
import qrcode
from qr_demo.qr_code import get_qr_code 
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
import os
from frappe.model.document import Document

class MemberRegistration(Document):
	
	@frappe.whitelist()
	def before_save(self):
		url = f'{self.name}'
		self.qr_code = get_qr_code(url)
	
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(url)
		qr.make(fit=True)
		qr_img = qr.make_image(fill_color="black", back_color="white")
		qr_img.save("qrcode.png")
		current_site_name = frappe.local.site
		html_content = """
			<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<style>
					body {{
						font-family: Arial, sans-serif;
						margin: 0;
						padding: 0;
						box-sizing: border-box;
						}}

						.card {{
						width: 600px;
						margin: 20px;
						padding: 15px;
						border: 2px solid #333;
						}}

						header {{
						display: flex;
						align-items: center;
						justify-content: center;
						text-align: center;
						}}

						header img {{
						max-width: 100px;
						max-height: 100px;
						margin-right: 10px; /* Adjust spacing between logo and company name */
						}}

						h1 {{
						margin: 10px 0;
						}}

						section p {{
						margin: 10px 0;
						padding-left:50px;
						}}

						footer {{
						text-align: center;
						}}

						.image_class{{
							margin-left: 40px;
						}}

						a:hover {{
						background-color: #007BFF;
						}}
						.instruction_class{{
							margin-left: 45px;
						}}			
				</style>
			</head>
				<body>
					<div class="card">
						<table style="margin-left: 110px;">
							<tr style="text-align: center;">
								<header>
									<td><img style="margin-top: 25px; height: 38px; width: auto;" src="https://{0}/private/files/TLC.png" alt="Company Logo"></td>
									<td style="text-align: center;"><h1>TLC Big Bash 2024</h1>
										<p >{1}</p>
									</td>
								</header>
							</tr>
						</table>

						<br>
						<section>
						<p><b>Name</b> : {2}</p>
						<p><b>Date </b>: {3}</p>
						<p><b>Level</b> : {4}</p>
						<p><b>City</b> : {5} </p>
						<p><b>Company Name</b> : {6}</p>
						<p><b>QR Code</b> :</p>
							 <div class="image_class"><img style=" height="10%" width="30%" src="{7}"/><br></div>
						</section>
						<br>
						<b style=" text-decoration: underline;"><a style=" padding-left:45px;" href="#" class="text-left-top">View Schedule</a> <br><br>
						<a style="padding-left:45px;"href="#" class="text-left-top;">Venue Direction</a></b><br>
						<div class="instruction_class">
							<br><b><p>Instructions :</p></b> 
							<ul>
							<li>Add Instriction Here-1</li>
							<li>Add Instriction Here-1</li>
							<li>Add Instriction Here-1</li>
							</ul>
						</div>
						<footer>
							
						</footer>
					</div>
					</body>
			</html>
		""".format(current_site_name,self.city,self.full_name,self.registration_date,self.tlc_level,self.city,self.company_name,self.qr_code)
		pdf_content = get_pdf(html_content, {'orientation': 'Portrait'})

		
		target_directory = frappe.get_site_path('public', 'files')
		os.makedirs(target_directory, exist_ok=True)
		check_exist_file=""
		if(self.pdf_name):
			check_exist_file=f"./{current_site_name}/public{self.pdf_name}"

		if os.path.exists(check_exist_file):
			attachment_name = frappe.get_value("File", {"file_url": self.pdf_name}, "name")
			if attachment_name:
				frappe.delete_doc("File", attachment_name, force=True, ignore_permissions=True)


		file_path = os.path.join(target_directory, f'{self.name}.pdf')
		with open(file_path, 'wb') as file:
			file.write(pdf_content) 
		
  
		file_doc = frappe.get_doc({
			'doctype': 'File',
			'file_name': f'{self.name}.pdf',
			'attached_to_doctype': self.doctype,
			'attached_to_name': self.name,
			'file_url': file_path,
			'content': pdf_content
		})
		file_doc.save(ignore_permissions=True)
		self.pdf_attachment = file_doc.file_url
		self.pdf_name=file_doc.file_url


		smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server address
		smtp_port = 25  # Replace with your SMTP server's port (587 for TLS)
		smtp_username = 'support@quantbit.io'  # Replace with your SMTP username
		smtp_password = 'xnia pefr nlmx cxwx'  # Replace with your SMTP password
		sender_email = 'support@quantbit.io'  # Replace with your email address
		receiver_email = self.email  # Replace with the recipient's email address

	# Create a message
		subject = 'QR Code'
		message = 'This is a QR code To '+ " " +self.full_name

		msg = MIMEMultipart()
		msg['From'] = 'Quantbit Technologies Pvt. Ltd.'
		msg['To'] = self.email
		msg['Subject'] = 'Event QR Code'

		msg.attach(MIMEText(message, 'plain'))

	# Attach the QR code image
		qr_filename = "qrcode.png"
		qr_attachment = open(qr_filename, "rb")
		qr_base = MIMEBase('application', 'octet-stream')
		qr_base.set_payload(qr_attachment.read())
		encoders.encode_base64(qr_base)
		qr_base.add_header('Content-Disposition', f'attachment; filename={qr_filename}')
		msg.attach(qr_base)
		
	
	# Connect to the SMTP server
		try:
			server = smtplib.SMTP(smtp_server, smtp_port)
			server.starttls()  # Enable TLS encryption
			server.login(smtp_username, smtp_password)
    
    # Send the em
			server.sendmail(sender_email, receiver_email, msg.as_string())
		except Exception as e:
			print(f'Email could not be sent. Error: {str(e)}')
		finally:
			server.quit()  # Close the SMTP server connection
   
