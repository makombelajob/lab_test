<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class ScanController extends AbstractController
{
    #[Route('/scan', name: 'app_scan')]
    public function index(): Response
    {
        return $this->render('scan/index.html.twig', [
            'controller_name' => 'ScanController',
            'output' => null
        ]);
    }
}
