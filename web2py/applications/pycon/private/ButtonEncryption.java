/*
 *
 */

import com.paypal.crypto.sample.*;

import java.io.*;
import java.security.InvalidAlgorithmParameterException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.Security;
import java.security.UnrecoverableKeyException;
import java.security.cert.CertStoreException;
import java.security.cert.CertificateException;
import org.bouncycastle.cms.CMSException;

/**
 */
public class ButtonEncryption 
{
	private static String keyPath = null;
	private static String certPath = null;
	private static String paypalCertPath = null;
	private static String keyPass = "password";
	private static String cmdText = null; 			//cmd=_xclick,business=sample@paypal.com,amount=1.00,currency_code=USD
	private static String output = "test.html";


	public static void main(String[] args) 
	{
		Security.addProvider(new org.bouncycastle.jce.provider.BouncyCastleProvider());	

		if ( args.length !=6 && args.length != 7 )
		{
			System.out.println ( "Usage: java ButtonEncryption <CertFile> <PrivKeyFile> <PPCertFile> <Password> <CmdTxt> <OutputFile> [sandbox]" );
			System.out.println ( "	CertFile:	Your Public Cert" );
			System.out.println ( "	PKCS12File:	Your Private Key in PKCS12 format" );
			System.out.println ( "	PPCertFile:	PayPal's Public Cert" );
			System.out.println ( "	KeyPassword:	Password to sign with the private Key" );	
			System.out.println ( "	CmdTxt:		The button command, eg: 'cmd=_xclick,business=...'" );
			System.out.println ( "	OutputFile:	File where the html will get written" );
			System.out.println ( "	Sandbox:	Optional. Put 'sandbox' here to test on sandbox accounts, or ");
			System.out.println ( "				leave blank for testing on live.");
			return;
		}

		certPath = args[0];
		keyPath = args[1];
		paypalCertPath = args[2];
		keyPass = args[3];
		cmdText = args[4];
		output = args[5];
		String stage = "";
		if ( args.length == 7 )
			stage = args[6] + ".";

		try 
		{
			ClientSide client_side = new ClientSide( keyPath, certPath, paypalCertPath, keyPass );

			String result = client_side.getButtonEncryptionValue( cmdText, keyPath, certPath, paypalCertPath, keyPass );
			
			File outputFile = new File( output );
			if ( outputFile.exists() )
				outputFile.delete();
			
			if ( result != null && result != "")
			{
				try {        
					OutputStream fout= new FileOutputStream( output );
			        OutputStream bout= new BufferedOutputStream(fout);
					OutputStreamWriter out = new OutputStreamWriter(bout, "US-ASCII");
			      
			        out.write( "<form action=\"https://www." );
			        out.write( stage );
			        out.write( "paypal.com/cgi-bin/webscr\" method=\"post\">" );  
			        out.write( "<input type=\"hidden\" name=\"cmd\" value=\"_s-xclick\">" );  ;
			        out.write( "<input type=\"image\" src=\"https://www." );
			        out.write( stage );
			        out.write( "paypal.com/en_US/i/btn/x-click-but23.gif\" border=\"0\" name=\"submit\" " );
			        out.write( "alt=\"Make payments with PayPal - it's fast, free and secure!\">" );
			        out.write( "<input type=\"hidden\" name=\"encrypted\" value=\"" );
			        out.write( result );
			        out.write( "\">" );
			        out.write( "</form>");
			       
			        out.flush();  // Don't forget to flush!
			        out.close();
			      }
			      catch (UnsupportedEncodingException e) {
			        System.out.println(
			         "This VM does not support the ASCII character set."
			        );
			      }
			      catch (IOException e) {
			        System.out.println(e.getMessage());        
			      }
			}
		} 
		catch (NoSuchAlgorithmException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (NoSuchProviderException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (IOException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (CMSException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (CertificateException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (KeyStoreException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (UnrecoverableKeyException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (InvalidAlgorithmParameterException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
		catch (CertStoreException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
