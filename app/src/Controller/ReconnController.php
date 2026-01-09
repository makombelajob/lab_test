<?php

namespace App\Controller;

use App\Repository\PingRepository;
use App\Service\PythonScriptRunner;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;


final class ReconnController extends AbstractController
{
    #[Route('/reconn', name: 'app_reconn')]
    public function index(
        PingRepository $pingRepository,
        PythonScriptRunner $pythonRunner
    ): Response {
        $this->denyAccessUnlessGranted('ROLE_USER');

        $lastPing = $pingRepository->findOneBy(
            ['user' => $this->getUser()],
            ['scanAt' => 'DESC']
        );

        $ipTarget = $lastPing?->getIpAddress();

        $output = null;
        $showResult = false;

        if ($ipTarget) {
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

                $output = $result['output'];
                $showResult = true;
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
