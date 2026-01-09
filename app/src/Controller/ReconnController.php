<?php

namespace App\Controller;

use App\Repository\PingRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\HttpFoundation\Request;


final class ReconnController extends AbstractController
{
    #[Route('/reconn', name: 'app_reconn')]
    public function index(PingRepository $pingRepository, Request $request): Response
    {
        $this->denyAccessUnlessGranted('ROLE_USER');

        // Récupération du dernier ping de l'utilisateur
        $lastPing = $pingRepository->findOneBy(
            ['user' => $this->getUser()],
            ['scanAt' => 'DESC']
        );

        $ipTarget = $lastPing?->getIpAddress();
        $hostname = $lastPing?->getHostname();

        $output = null;
        $showResult = false;

        if ($ipTarget) {
            // Chemins Python
            /**
             * @var \App\Entity\User $user
             */
            $user = $this->getUser();
            $userId = $user->getId();
            $pyBin = '/opt/venv/bin/python3';
            $pyScript = 'scripts/reconn/emailfound.py'; // chemin relatif si fichier
            $projectRoot = $this->getParameter('kernel.project_dir');

            // Vérification du binaire Python et du projet
            if (!file_exists($pyBin)) {
                $this->addFlash('danger', "⚠️ Python env not found at $pyBin!");
            } elseif (!is_dir($projectRoot)) {
                $this->addFlash('danger', "⚠️ Project root directory not found at $projectRoot!");
            } else {
                // Exécution du script Python
                $command = sprintf(
                    'cd %s && %s %s %d %s 2>&1',
                    escapeshellarg($projectRoot),
                    escapeshellarg($pyBin),
                    escapeshellarg($pyScript),
                    $userId,
                    escapeshellarg($ipTarget)
                );

                $output = shell_exec($command);
                $showResult = true;

                // Flash message pour affichage
                //$this->addFlash('success', "Email Found");
            }
        }

        return $this->render('reconn/index.html.twig', [
            'showResult' => $showResult,
            'output' => $output
        ]);
    }
}
