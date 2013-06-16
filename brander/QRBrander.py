###
### Uses the python-qrcode library to generate the initial QR code
###     and PIL to do the rest of the work
###
### Usage: python QRBrander.py [logo_filepath] [max_width] [output_filename] [data]
### 		logo_filepath -> file path to logo image to brand the QR with
###			max_width -> a single integer representing size of QR to generate in pixels
###			output_filename -> what to name the branded QR to be saved in the "branded/" directory
###			data -> data to encode
###
### Example: python QRBrander.py logos/metlogo.png 350 met_branded A message to encode


import sys
from PIL import Image
import qrcode, re


#validate the data we want to encode in the QR code
def validateQRData(data):
	pattern = re.compile("^[0-9A-Za-z$%*+-./:\s]*$")

	if pattern.match(data):
		return True
	
	return False

def setTransparency(img, alpha):
	w,h = img.size
	pixels = img.load()
	for x in range(0,w):
		for y in range(0,h):
			pix = pixels[x,y]
			if not pix[3] == 0:
				pixels[x,y] = (pix[0],pix[1],pix[2], int(255*alpha))

	return img


def createImages(total_size, block_size, alignment_block_data, logo_fname):
	#Image sizes in pixels
	total_pix_size = total_size * block_size
	pos_block_pix_size = 8 * block_size
	align_block_pix_size = 5 * block_size

	#Load the images to be worked with
	base_logo = Image.open(logo_fname)
	base_pos_block = Image.open("../brander/images/position_block.png")
	base_align_block = Image.open("../brander/images/alignment_block.png")
	base_black_square = Image.open("../brander/images/smallSquare.png")
	base_white_square = Image.open("../brander/images/smallSquareWhite.png")

	#Resize images to needed dimensions and transparency
	resized_logo = base_logo.resize((total_pix_size, total_pix_size), Image.ANTIALIAS)
	resized_logo_light= setTransparency(resized_logo.copy(), .2)
	resized_pos_block = base_pos_block.resize((pos_block_pix_size, pos_block_pix_size), Image.ANTIALIAS)

	resized_align_block = base_align_block.resize((align_block_pix_size, align_block_pix_size), Image.ANTIALIAS)
	resized_black_square = base_black_square.resize((block_size, block_size), Image.ANTIALIAS)
	resized_white_square = base_white_square.resize((block_size, block_size), Image.ANTIALIAS)

	#Thq main image object we will be editing and adding to
	constant_layer = Image.new("RGBA", (total_pix_size, total_pix_size), (255,255,255,0))

	#Add position blocks to constant layer
	constant_layer.paste(resized_pos_block, (0, 0)) #top-left
	constant_layer.paste(resized_pos_block.rotate(90), (0, total_pix_size - pos_block_pix_size)) #top-right
	constant_layer.paste(resized_pos_block.rotate(-90), (total_pix_size - pos_block_pix_size, 0)) #bottom-left

	#Add alignment blocks to constant layer
	for a_block in alignment_block_data:
		constant_layer.paste(resized_align_block, (a_block[0] * block_size, a_block[1] * block_size))

	#Make a copy of current state before applying the first logo overlay
	critical_data = constant_layer.copy()

	#Add inital logo overlay
	constant_layer.paste(resized_logo_light, (0,0), resized_logo_light)

	#Add logo overlay at 50% transparency only to critical data areas
	for x in range(0,total_pix_size):
		for y in range(0,total_pix_size):
			pix = critical_data.getpixel((x,y))
			if pix == (255,255,255,0):
				constant_layer.putpixel((x,y), (255,255,255,0))

	#Return an array of the created images
	return [resized_logo, constant_layer, critical_data, resized_black_square, resized_white_square]


def createBrandedQR(data, max_width, logo_fname, out_file):
	#Validate data
	if not validateQRData(data):
		print "invalid data"
		sys.exit()

	#Constants
	margin_multiplier = 4 #White space around image in blocks

	#Determine what version of qr we need and declare necessary variables
	if len(data) <= 0:
		#unsupported message length
		print "no data given"
		sys.exit()

	elif len(data) <= 17:
		#Version 1 (Message length >= 1 but <= 17)
		version = 1
		size = 21 #QR image size in blocks
		align_data_points = [] #Position of alignment blocks

	elif len(data) <= 32:
		#Version 2 (Message length >= 18 but <= 32)
		version = 2
		size = 25
		align_data_points = [(16,16)]

	elif len(data) <= 53:
		#Version 3 (Message length >= 33 but <= 53)
		version = 3
		size = 29
		align_data_points = [(20,20)]

	elif len(data) <= 78:
		#Version 4 (Message length >= 54 but <= 78)
		version = 4
		size = 33
		align_data_points = [(24,24)]

	elif len(data) <= 106:
		#Version 5 (Message length >= 79 but <= 106)
		version = 5
		size = 37
		align_data_points = [(28,28)]

	elif len(data) <= 134:
		#Version 6 (Message length >= 107 but <= 134)
		version = 6
		size = 41
		align_data_points = [(32,32)]

	elif len(data) <= 154:
		#Version 7 (Mesage length >= 135 but <= 154)
		version = 7
		size = 45
		align_data_points = [(20,4),(4,20),(20,20),(36,20),(20,36),(36,36)]

	else:
		#unsupported message length
		print "invalid message length"
		sys.exit()


	#More constants
	block_size = max_width // size #Size of individual block
	margin = margin_multiplier * block_size #White space around image in pixels
	canvasSize = (size+(margin_multiplier*2))*block_size #Size of entire image

	#Create the blank canvas for it all to go on
	brandedQR = Image.new("RGBA", (canvasSize, canvasSize), (255,255,255))

	#Create the images needed for the branding of the QR
	created_images = createImages(size, block_size, align_data_points, logo_fname)

	resized_logo = created_images[0]
	constant_layer = created_images[1]
	critical_data = created_images[2]
	darkSquare = created_images[3]
	lightSquare = created_images[4]

	#Generate QR code with python qrcode library
	qr = qrcode.QRCode(
		version=version, #should be automatic but doesn't hurt to specify
	    error_correction=qrcode.ERROR_CORRECT_L, #All constants are based of EC being type 'L'
	    box_size=block_size,
	)
	qr.add_data(data)
	qr.make(fit=True)

	QRimg = qr.make_image()

	#Add the primary logo layer first
	brandedQR.paste(resized_logo, (margin, margin), resized_logo)
			
	#Add the QR code layer next
	for x in range(0,size):
		xPix = (x * block_size) + margin #x pixel value of current block
		for y in range(0,size):
			yPix = (y * block_size) + margin #y pixel value of current block
			pix = QRimg.getpixel((xPix+(block_size/2),yPix+(block_size/2)))
			
			critical_pix = critical_data.getpixel((xPix-margin+7,yPix-margin+7))
			if critical_pix == (255,255,255,0):
				#black
				if pix == 0:
					brandedQR.paste(darkSquare, (xPix, yPix), darkSquare)
				#white
				else:
					brandedQR.paste(lightSquare, (xPix, yPix), lightSquare)

	#Add the final constant layer
	brandedQR.paste(constant_layer, (margin, margin), constant_layer)


	#Save the image
	brandedQR.save(out_file)






if __name__ == '__main__':

	args = sys.argv[1:]
	if args:
		try:
			logo_fname = args[0]
			max_width = int(args[1])
			out_file = args[2]
			data = args[3]
			
			i = 4
			while i < len(args):
				data += " " + args[i]
				i += 1

			createBrandedQR(data, max_width, logo_fname, out_file)
		except Exception as e:
			#print "Usage: python QRBrander.py [logo_filepath] [max_width] [output_filename] [data]"
			print e
			sys.exit()
	else:
		print "Usage: python QRBrander.py [logo_filepath] [max_width] [output_filename] [data]"
		sys.exit()



