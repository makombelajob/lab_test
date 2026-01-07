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
       // Only connected user can scan
       $this->denyAccessUnlessGranted('ROLE_USER');

       // New ping scan
       $ping = new Ping();
       $form = $this->createForm(PingType::class, $ping);
       $form->handleRequest($request);

        // Set session for python output
        $session = $request->getSession();
        $output = $session->get('python_output', null);
        // Remove output after refresh
        $session->remove('python_output');

        // Verify the form input content
        if ($form->isSubmitted() && $form->isValid()) {

           $target = $form->get('hostname')->getData();

           // Cas 1️⃣ : l'utilisateur a saisi une IP
           if (filter_var($target, FILTER_VALIDATE_IP)) {
               $ping->setIpAddress($target);
               $ping->setHostname(null);
           }
              // Cas 2️⃣ : l'utilisateur a saisi un domaine
              else {
                  $ping->setHostname($target);
                  $ping->setIpAddress(null);
              }

              // 3️⃣ Date automatique (si pas déjà fait)
              $ping->setScanAt(new \DateTimeImmutable());

              $ping->setUser($this->getUser());

              // 5️⃣ Sauvegarde
              $entity->persist($ping);
              $entity->flush();

              /**
                * Construct python command
              */

              $userId = $this->getUser()->getId();
              $pyBin = '/opt/venv/bin/python3';
              $pyModule = 'scripts.ping.pingtarget';
              $projectRoot = $this->getParameter('kernel.project_dir');

              ## Verification of python file
              if (!file_exists($pyBin)) {
                  return new Response("🤦‍♂️ Python env Not found !");
              }

              if (!is_dir($projectRoot . '/scripts')) {
                   return new Response("🤦‍♂️ Python scripts directory not found !");
              }
              $command = sprintf(
                  'cd %s && %s -m %s %d %s 2>&1',
                  escapeshellarg($projectRoot),
                  escapeshellcmd($pyBin),
                  escapeshellarg($pyModule),
                  $userId,
                  escapeshellarg($target)
              );

              $output = shell_exec($command);
              // Save the python output
              $session->set('python_output', $output);

              $this->addFlash('success', 'Ping exécuté');

              return $this->redirectToRoute('app_ping');
        }

        return $this->render('ping/index.html.twig', ['form' => $form->createView(), 'output' => $output]);
    }
}
