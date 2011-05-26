import tarfile,zipfile,shutil,os,ConfigParser
config=ConfigParser.ConfigParser()
config.read('VERSION')
version=config.get('Version','VERSION')                 #N.N.N.N format version number
f='YARDWiz-'+'.'.join(version.split('.')[:-1])
os.chdir(r'dist')
zip=zipfile.ZipFile(f+'.zip','r')
tar = tarfile.open(f+'-linux.tar.gz', 'w:gz')
zip.extractall()
shutil.copyfile('../buildfiles/getWizPnP-linux',f+'/getWizPnP')
tar.add(f)
tar.close()
zip.close()
shutil.rmtree(f)

