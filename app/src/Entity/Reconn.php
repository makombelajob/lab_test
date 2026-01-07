<?php

namespace App\Entity;

use App\Repository\ReconnRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ReconnRepository::class)]
class Reconn
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $emailFound = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $userFound = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $pathFound = null;

    #[ORM\ManyToOne(inversedBy: 'reconn')]
    #[ORM\JoinColumn(nullable: false)]
    private ?User $user = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getEmailFound(): ?string
    {
        return $this->emailFound;
    }

    public function setEmailFound(?string $emailFound): static
    {
        $this->emailFound = $emailFound;

        return $this;
    }

    public function getUserFound(): ?string
    {
        return $this->userFound;
    }

    public function setUserFound(?string $userFound): static
    {
        $this->userFound = $userFound;

        return $this;
    }

    public function getPathFound(): ?string
    {
        return $this->pathFound;
    }

    public function setPathFound(?string $pathFound): static
    {
        $this->pathFound = $pathFound;

        return $this;
    }

    public function getUser(): ?User
    {
        return $this->user;
    }

    public function setUser(?User $user): static
    {
        $this->user = $user;

        return $this;
    }
}
