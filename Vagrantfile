# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.define "ubuntu" do |ubuntu|
    ubuntu.vm.box = "ubuntu/trusty64"

    ubuntu.vm.define :UbuntuHost do |host|
    end

    ubuntu.vm.network "forwarded_port", guest: 80, host: 8080
    ubuntu.vm.network "forwarded_port", guest: 443, host: 8443

    ubuntu.vm.provider "virtualbox" do |vb|
       vb.memory = "512"
       vb.name = "AnsibleLP-Lab2"
     end
  
     ubuntu.vm.provision "shell", inline: <<-SHELL
       sudo apt-get update
       sudo apt-get -y dist-upgrade
       sudo apt-get -y install git
     SHELL
  end

  config.vm.provision "ansible_local" do |ansible|
    ansible.install = true
    ansible.install_mode = ":pip"
    ansible.playbook = "blank.yml"
  end

end
