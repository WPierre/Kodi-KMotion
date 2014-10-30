XBMC-K-Net : Plugin XBMC/KODI pour KMotion
==========================================

XBMC-KMotion est un plugin vous permettant d'accéder à la plateforme de partage de vidéos [KMotion.fr]. Un compte KMotion est nécessaire pour utliser ce plugin.

Notes
-----

Ce plugin est en version beta et comporte moins de fonctionnalités que le site Web. La création de playlist et l'adhésion aux communautés se font sur le site web uniquement.

A été testé avec XBMC Gotham (13.2) sous Windows et Linux (Ubuntu 14.04) 

Si vous rencontrez des problèmes, n'hésitez pas à ouvrir un ticket dans la section "Issues" en haut à droite ou à en discuter sur le [forum K-Net].
Pour toute remontée de bugs, merci de fournir le fichier de logs d'XBMC. Il se trouve dans c:\Utilisateurs\\[nom]\\AppDatas\Roaming\XBMC\xbmc.log sous Windows et /home/[nom]/.xbmc/xbmc.log sous Linux.

Installation
------------

Si vous ne connaissez pas XBMC, il est préférable de revenir plus tard, lorsque des tests plus poussés auront été menés.
 
  - Commencez par télécharger le [fichier zip du dépôt XBMC] et sauvegardez le sur le disque dur.
  - Lancez XBMC et allez dans "Système" -> "Extensions" -> "Installer depuis un fichier zip"
  - Avec la fenêtre qui s'ouvre, naviguez sur votre disque dur jusqu'au fichier zip du dépôt, puis cliquez sur OK
  - Une notification devrait apparaître en bas à droite disant que l'extension "XBMC K-Net Addons" est installée.
  - Cliquez sur le bouton "Maison" en bas à droite de l'écran.
  - Allez dans Vidéos -> Extensions -> plus..., puis cliquez deux fois de suite sur ".."
  - Cliquez sur "Télécharger des extensions", puis "XBMC K-Net Addons" -> "Extensions Vidéo" -> "KMotion XBMC" et "installer".
  - Au passage, cliquer sur "configurer" et saisissez votre login et votre mot de passe. Le plugin vous les redemandera plus tard si vous ne les avez pas renseignés.

Lancer le plugin
----------------

A partir de l'écran d'accueil d'XBMC, allez dans "Vidéos" -> "Extensions" -> "KMotion XBMC"

Bugs connus
-----------

  - J'arrive à naviguer avec l'extension, mais je n'arrive pas à lire une vidéo => Certaines vidéos ne sont pas disponibles sur le site. Si le problème se reproduit avec plusieurs vidéos, vérifier que le login que vous avez saisi dans les options respecte bien les minuscules et majuscules de votre pseudo sur le site.
  - Sous Windows, lorsque j'accède à une communauté avec beaucoup de vidéos, certaines vignettes ne s'affichent que lorsque je passe la souris dessus (mode vignette et large) => C'est un bug d'XBMC, il faut malheureusement attendre que l'équipe XBMC corrige le problème.


[KMotion.fr]:http://www.kmotion.fr
[fichier zip du dépôt XBMC]:https://github.com/WPierre/Kodi-KMotion/raw/master/repository.knet/repository.knet-1.0.6.zip
[forum K-Net]:http://forum.k-net.fr