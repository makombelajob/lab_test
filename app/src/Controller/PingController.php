<?php

namespace App\Controller;

use App\Entity\Ping;
use App\Form\PingType;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\HttpFoundation\Request;

final class PingController extends AbstractController
{
    #[Route('/ping', name: 'app_ping')]
    public function index(Request $request, EntityManagerInterface $entity): Response
    {
        $this->denyAccessUnlessGranted('ROLE_USER');

        $ping = new Ping();
        $form = $this->createForm(PingType::class, $ping);
        $form->handleRequest($request);

        $session = $request->getSession();
        $output = $session->get('python_output', null);
        $session->remove('python_output');

        if ($form->isSubmitted() && $form->isValid()) {

            $target = $form->get('hostname')->getData();

            /**
             * @var \App\Entity\User $user
             */
            $user = $this->getUser();
            $userId = $user->getId();

            $pyBin = '/opt/venv/bin/python3';
            $pyModule = 'scripts.ping.pingtarget';
            $projectRoot = $this->getParameter('kernel.project_dir');

            if (!file_exists($pyBin)) {
                return new Response("Python env not found");
            }

            if (!is_dir($projectRoot . '/scripts')) {
                return new Response("Python scripts directory not found");
            }

            // Commande Python
            $command = sprintf(
                'cd %s && %s -m %s %d %s 2>&1',
                escapeshellarg($projectRoot),
                escapeshellcmd($pyBin),
                escapeshellarg($pyModule),
                $userId,
                escapeshellarg($target)
            );

            // Récupération de la sortie Python
            $output = shell_exec($command);

            // Séparation texte ping (UI) et ping_data pour DB
            $parts = explode("\n@@@PINGJSON@@@\n", $output);

            if (count($parts) !== 2) {
                return new Response("<pre>Python output:\n" . htmlspecialchars($output) . "</pre>");
            }

            $uiOutput = $parts[0];       // texte pour l’affichage
            $jsonData = trim($parts[1]); // ping_data pour la DB

            $data = json_decode($jsonData, true);
            if (!$data) {
                return new Response("<pre>Invalid Python JSON:\n" . htmlspecialchars($jsonData) . "</pre>");
            }

            // Stockage dans l’entité Ping
            $ping->setHostname($data['hostname'] ?? null);
            $ping->setIpAddress($data['ipAddress'] ?? null);
            $ping->setStatus(isset($data['status']) ? (bool)$data['status'] : null);
            $ping->setScanAt(new \DateTimeImmutable());
            $ping->setUser($user);

            $entity->persist($ping);
            $entity->flush();

            // Texte du ping pour l’UI
            $session->set('python_output', $uiOutput);

            $this->addFlash(
                'success',
                'Ping exécuté. Cliquez sur Reconn dans 30 secondes.'
            );

            return $this->redirectToRoute('app_ping');
        }

        return $this->render('ping/index.html.twig', [
            'form' => $form->createView(),
            'output' => $output
        ]);
    }
}
