<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class ReconnController extends AbstractController
{
    #[Route('/reconn', name: 'app_reconn')]
    public function index(): Response
    {
        return $this->render('reconn/index.html.twig', [
            'controller_name' => 'ReconnController',
        ]);
    }
}
