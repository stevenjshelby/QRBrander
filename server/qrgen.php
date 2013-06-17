<?php

	$logo = $_POST['filedata'];
	$filename = str_replace("\"","'",$_POST['filename']);
	$qrdata = urlencode($_POST['qrdata']);

	$serverLogo = time().$filename;
	$serverBranded = "b_".$serverLogo;

	$logo = str_replace('data:image/png;base64,', '', $logo);
	$logo = str_replace(' ', '+', $logo);

	$logodata = base64_decode($logo);

	$fp = fopen('logos/'.$serverLogo,'w'); //Prepends timestamp to prevent overwriting
	fwrite($fp, $logodata);
	fclose($fp);

	$scriptdata = shell_exec('python ../brander/QRBrander.py logos/'.$serverLogo.' 400 branded/'.$serverBranded.' '.$qrdata);

	$returnData = array( "serverLogo" => $serverLogo, "serverBranded" => $serverBranded );
	echo json_encode($returnData);

?>