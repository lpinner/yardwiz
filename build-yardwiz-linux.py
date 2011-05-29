import tarfile,zipfile,shutil,os,ConfigParser
config=ConfigParser.ConfigParser()
config.read('VERSION')
version=config.get('Version','VERSION')                 #N.N.N.N format version number
f='YARDWiz-'+'.'.join(version.split('.')[:-1])
os.chdir(r'dist')
zip=zipfile.ZipFile(f+'.zip','r')
zip.extractall()
zip.close()
for arch in ['86','64']:
    tar = tarfile.open(f+'-linux-x%s.tar.gz'%arch, 'w:gz')
    shutil.copyfile('../buildfiles/getWizPnP-linux-x%s'%arch,f+'/getWizPnP')
    tar.add(f)
    tar.close()
shutil.rmtree(f)

