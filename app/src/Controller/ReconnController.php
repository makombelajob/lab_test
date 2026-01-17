<?php

namespace App\Controller;

use App\Entity\Reconn;
use App\Repository\PingRepository;
use App\Service\PythonScriptRunner;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class ReconnController extends AbstractController
{
    #[Route('/reconn', name: 'app_reconn')]
    public function index(
        PingRepository $pingRepository,
        PythonScriptRunner $pythonRunner,
        EntityManagerInterface $entityManager
    ): Response {
        $this->denyAccessUnlessGranted('ROLE_USER');

        $lastPing = $pingRepository->findOneBy(
            ['user' => $this->getUser()],
            ['scanAt' => 'DESC']
        );

        $ipTarget = $lastPing?->getIpAddress();

        $output = null;
        $showResult = false;

        if ($ipTarget && $lastPing) {
            try {
                /**
                 * @var \App\Entity\User $user
                 */
                $user = $this->getUser();
                $userId = $user->getId();

                $result = $pythonRunner->run(
                    'scripts/reconn/emailfound.py',
                    $userId,
                    $ipTarget
                );

                $outputFull = $result['output'];

                // ====================== Séparation texte et JSON ======================
                $parts = explode("\n@@@RECONNJSON@@@\n", $outputFull);

                $uiOutput = $parts[0]; // texte classique pour Twig
                $jsonData = $parts[1] ?? null;

                $output = $uiOutput;
                $showResult = true;

                if ($jsonData) {
                    $data = json_decode($jsonData, true);

                    if ($data) {
                        // Vérifie si un record Reconn existe déjà pour ce ping
                        $reconn = $lastPing->getReconn()->first() ?: new Reconn();
                        $reconn->setPing($lastPing);
                        $reconn->setEmailFound(isset($data['emails']) ? implode(', ', $data['emails']) : '');
                        $reconn->setUserFound(isset($data['users']) ? implode(', ', $data['users']) : '');
                        $reconn->setLinkFound(isset($data['links']) ? implode(', ', $data['links']) : '');

                        // Persist seulement si nouveau
                        if (!$reconn->getId()) {
                            $entityManager->persist($reconn);
                        }

                        $entityManager->flush();
                    }
                }
            } catch (\RuntimeException $e) {
                $this->addFlash('danger', $e->getMessage());
            }
        }

        return $this->render('reconn/index.html.twig', [
            'showResult' => $showResult,
            'output' => $output
        ]);
    }
}